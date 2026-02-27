-- AlterTable
ALTER TABLE "public"."auctions" ADD COLUMN     "scheduledAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;
